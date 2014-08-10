define(["jquery", "lodash", "knockout", "text!components/matching.html"], function ($, _, ko, template) {
    var forms = {}, currentItem = ko.observable();

    $(document).on("click", ".match-modal-button", function () {
        var data = $(this).data();
        currentItem({ id: data.itemId, type: data.itemType });
    });

    ko.components.register("matching-form", {
        viewModel: function (params) {
            return forms[params.id] || (forms[params.id] = new MatchForm(params));
        },
        template: template
    });

    function MatchForm(params) {
        forms[params.id] = this;

        this.itemID = params.id;
        this.itemType = params.type;
        this.newMatch = ko.observable(new Match({}, this));
        this.currentMatch = ko.observable(this.newMatch.peek().toJS());
        this.previousMatches = ko.observableArray([]);
        this.allowEmptyMatch = ko.observable(false);
        this.submissionLoading = ko.observable(false);
        this.submissionError = ko.observable("");
        this.submissionSuccess = ko.observable(false);
        this.getMatches();
    }

    MatchForm.prototype.canSubmit = function () {
        return !(
            this.submissionLoading() ||
            this.hasErrors() ||
            (this.newMatch().allFieldsAreEmpty() && !this.allowEmptyMatch())
        );
    };

    MatchForm.prototype.hasErrors = function () {
        return !_.all(this.newMatch().entities(), function (entity) {
            return !entity.hasInvalidMBID() && !entity.loadError();
        });
    };

    MatchForm.prototype.getMatches = function () {
        var self = this;

        $.get("/item/" + this.itemID + "/matches", function (data) {
            var currentMatch = new Match(data.currentMatch || {}, self);

            self.currentMatch(currentMatch.toJS());

            currentMatch.addEmptyField();

            self.newMatch(currentMatch);

            self.previousMatches(
                _.map(data.previousMatches, function (data) { return new Match(data, self) })
                .sort(function (a, b) { return b.timestamp - a.timestamp })
            );
        });
    };

    MatchForm.prototype.submit = function () {
        var mbids = _.filter(_.invoke(this.newMatch().entities(), "mbid"), isMBID);
        var self = this;

        this.submissionLoading(true);
        this.submissionSuccess(false);

        $.ajax({
            type: "POST",
            url: "/item/" + this.itemID + "/match",
            contentType : "application/json",
            data: JSON.stringify({ matches: mbids, empty: mbids.length === 0 }),
        })
        .done(function (response) {
            if (response.error) {
                self.submissionError(response.error);
            } else {
                self.submissionSuccess(true);
                self.submissionError("");
                self.getMatches();
            }
        })
        .fail(function (jqXHR) {
            self.submissionError(jqXHR.responseText);
        })
        .always(function () {
            self.submissionLoading(false);
        });
    };

    function Match(data, form) {
        var self = this;

        _.assign(this, data);

        this.form = form;
        this.timestamp = new Date(data.timestamp);

        this.entities = ko.observableArray(
            _.map(data.entities, function (data) {
                return new Entity(data, self);
            })
        );
    }

    Match.prototype.emptyFieldCount = function () {
        return _.reject(_.invoke(this.entities(), "data")).length;
    };

    Match.prototype.allFieldsAreEmpty = function () {
        return this.emptyFieldCount() === this.entities().length;
    };

    Match.prototype.addEmptyField = function () {
        if (this.emptyFieldCount() === 0) {
            this.entities.push(new Entity({ type: this.form.itemType }, this));
        }
    };

    Match.prototype.toJS = function () {
        return {
            id: this.id,
            item: this.item,
            superseded: !!this.superseded,
            timestamp: this.timestamp.toString(),
            entities: _.invoke(this.entities(), "toJS")
        };
    };

    function Entity(data, match) {
        this.match = match;
        this.type = data.type;
        this.mbid = ko.observable(data.mbid || "");
        this.data = ko.observable(data.data);
        this.loading = ko.observable(false);
        this.loadError = ko.observable("");
        this.mbid.subscribe(this.mbidChanged, this);
    }

    Entity.prototype.entityURL = function () {
        return "https://musicbrainz.org/" + this.type + "/" + this.mbid();
    };

    Entity.prototype.mbidChanged = function (mbid) {
        this.loadError("");

        if (!mbid || this.ignoreChanges) {
            return;
        }

        this.data(null);

        if (mbid = mbid.match(mbidRegex)) {
            mbid = mbid[0];
            this.ignoreChanges = true;
            this.mbid(mbid);
            this.ignoreChanges = false;
        } else {
            return;
        }

        var self = this;
        this.loading(true);

        $.get("/entity/" + mbid + "?no_cache=true&type_hint=" + this.match.form.itemType)
            .done(function (data) {
                self.ignoreChanges = true;
                self.mbid(data.entity.mbid);
                self.ignoreChanges = false;
                self.data(data.entity.data);
                self.match.addEmptyField();
            })
            .fail(function (data) {
                self.data(null);
                self.loadError("Not found");
            })
            .always(function () {
                self.loading(false);
            });
    };

    Entity.prototype.hasInvalidMBID = function () {
        var mbid = this.mbid();
        return mbid ? !isMBID(mbid) : false;
    };

    Entity.prototype.remove = function () {
        this.match.entities.remove(this);
    };

    Entity.prototype.toJS = function () {
        return {
            type: this.type,
            mbid: this.mbid(),
            data: _.clone(this.data())
        };
    };

    var mbidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/;

    function isMBID(str) {
        return mbidRegex.test(str);
    }

    ko.applyBindings({ currentItem: currentItem });
});

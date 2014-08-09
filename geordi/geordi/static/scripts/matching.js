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
        this.currentMatch = ko.observable(new Match({}));
        this.previousMatches = ko.observableArray([]);
        this.submissionLoading = ko.observable(false);
        this.submissionError = ko.observable("");
        this.submissionSuccess = ko.observable(false);
        this.getMatches();

        var self = this;

        ko.computed(function () {
            if (self.emptyFieldCount() === 0) {
                var currentMatch = self.currentMatch();
                currentMatch.entities.push(new Entity({ type: self.itemType }, currentMatch));
            }
        });
    }

    MatchForm.prototype.canSubmit = function () {
        return !(
            this.submissionLoading() ||
            this.hasErrors() ||
            this.emptyFieldCount() === this.currentMatch().entities().length
        );
    };

    MatchForm.prototype.hasErrors = function () {
        return !_.all(this.currentMatch().entities(), function (entity) {
            return !entity.hasInvalidMBID() && !entity.loadError();
        });
    };

    MatchForm.prototype.emptyFieldCount = function () {
        return _.reject(_.invoke(this.currentMatch().entities(), "data")).length;
    };

    MatchForm.prototype.getMatches = function () {
        var self = this;

        $.get("/item/" + this.itemID + "/matches", function (data) {
            var currentMatch = new Match(data.currentMatch || {});

            if (!data.currentMatch) {
                currentMatch.entities.push(new Entity({}, currentMatch));
            }

            self.currentMatch(currentMatch);

            self.previousMatches(
                _.map(data.previousMatches, function (data) { return new Match(data) })
                .sort(function (a, b) { return b.timestamp - a.timestamp })
            );
        });
    };

    MatchForm.prototype.submit = function () {
        var mbids = _.filter(_.invoke(this.currentMatch().entities(), "mbid"), isMBID);

        if (mbids.length) {
            var self = this;

            this.submissionLoading(true);
            this.submissionSuccess(false);

            $.ajax({
                type: "POST",
                url: "/item/" + this.itemID + "/match",
                contentType : "application/json",
                data: JSON.stringify({ matches: mbids }),
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
        }
    };

    function Match(data) {
        var self = this;

        _.assign(this, data);

        this.timestamp = new Date(data.timestamp);

        this.entities = ko.observableArray(
            _.map(data.entities, function (data) {
                return new Entity(data, self);
            })
        );
    }

    function Entity(data, parent) {
        this.parent = parent;
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

        $.get("/entity/" + mbid + "?no_cache=true&type_hint=" + this.parent.itemType)
            .done(function (data) {
                self.ignoreChanges = true;
                self.mbid(data.entity.mbid);
                self.ignoreChanges = false;
                self.data(data.entity.data);
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
        this.parent.entities.remove(this);
    };

    var mbidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/;

    function isMBID(str) {
        return mbidRegex.test(str);
    }

    ko.applyBindings({ currentItem: currentItem });
});

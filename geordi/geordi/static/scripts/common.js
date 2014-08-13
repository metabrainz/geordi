require.config({
    paths: {
        jquery: "lib/jquery",
        bootstrap: "lib/bootstrap",
        knockout: "lib/knockout",
        lodash: "lib/lodash",
        text: "lib/require.text",
        components: "../components"
    },
    shim: {
        bootstrap: { deps: ["jquery"] }
    }
});

define(["jquery", "bootstrap"], function ($) {
    // Code that runs on every page.

    // Activates tooltip in the navbar.
    $("#remember").tooltip();
});

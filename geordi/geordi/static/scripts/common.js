require.config({
    paths: {
        jquery: "lib/jquery",
        bootstrap: "lib/bootstrap",
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

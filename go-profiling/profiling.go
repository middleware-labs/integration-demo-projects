package main

import (
	"context"
	"fmt"
	"net/http"
	"time"

	mwhttp "github.com/middleware-labs/golang-apm-http/http"
	otellog "github.com/middleware-labs/golang-apm/mwotellogrus"
	track "github.com/middleware-labs/golang-apm/tracker"
	log "github.com/sirupsen/logrus"
)

func StandardFields(ctx context.Context) log.Fields {
	return log.Fields{
		// "trace_id": track.TraceID(ctx),
		// "tid":      track.TraceID(ctx),
		// "sid":      track.SpanID(ctx),
		// "span_id":  track.SpanID(ctx),
		// "tes_attr":        "testing",
		otellog.MWTraceID: track.TraceID(ctx),
		otellog.MWSpanID:  track.SpanID(ctx),
	}
}

func main() {

	config, _ := track.Track(
		track.WithConfigTag(track.Service, "s2"),
		track.WithConfigTag(track.Project, "golang-logrus-service"),
		// track.WithConfigTag(track.Token, "zuxpjjypnejbbwhkvkobudfitutobptgonae"), // kgcgk
		// track.WithConfigTag(track.Token, "kqepimwfqqkqhszrqkvlbvevskojjbznbjml"), // nlruf
		// track.WithConfigTag(track.Token, "myimuvbvhfzvevleucdxhewjqmyiqzhckgol"), //cwext
		// track.WithConfigTag(track.Token, "lneevcqdcnzccpdpbhelkxpjffdxeznkryvb"), //cwext
		track.WithConfigTag(track.Token, "zuxpjjypnejbbwhkvkobudfitutobptgonae"),
		track.WithConfigTag(track.Target, "kgcgk.middleware.io:443"),
		track.WithConfigTag(track.Debug, true),
		track.WithConfigTag(track.DebugLogFile, true),
	)
	// lneevcqdcnzccpdpbhelkxpjffdxeznkryvb
	logHook := otellog.NewMWOTelHook(config, otellog.WithLevels(log.AllLevels), otellog.WithName("otellogs"))

	// add hook in logrus
	log.AddHook(logHook)
	// set formatter
	log.SetFormatter(&log.JSONFormatter{})

	//use mwhttp for http handler instrumentation
	http.Handle("/hello", mwhttp.MiddlewareHandler(http.HandlerFunc(helloHandler), "hello"))
	fmt.Println("listening on 8090")

	// this make continuos requests
	go makeRequest()

	// start the server
	http.ListenAndServe(":8090", nil)
}

func helloHandler(w http.ResponseWriter, r *http.Request) {

	time.Sleep(2 * time.Second)
	//set context in logrus for correlation
	logger := log.WithFields(StandardFields(r.Context()))

	logger.Info("GO12345678 Info helloHandler testing 123456")
	logger.Debug("GO12345678 Debug helloHandler testing 123456")
	logger.Error("GO12345678 Error helloHandler testing 123456")

	fmt.Fprintf(w, "Hello, World!")
}

func makeRequest() {
	for {
		time.Sleep(1 * time.Second)
		http.Get("http://localhost:8090/hello")
	}
}

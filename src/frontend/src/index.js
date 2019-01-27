import React from 'react';
// import ReactDOM from 'react-dom';
import * as serviceWorker from './serviceWorker';

import './index.css';
import ff from './ff.js';


let Project = function({mc, project}) {
    return (
        <div className="project">
            <h2><a href={"/project/" + project.uid + "/"} >{project.title}</a></h2>
        </div>
    )
}

let indexInit = async function(app, model) {
    let response = await ff.get("/api/projects/");
    let json = await response.json();
    return (app, model) => ff.Immutable(json);
}

let IndexView = function(model, mc) {
    return (
        <div id="container" className="index">
            <h1>lastho.pe</h1>
            <div>
                {model.map(project => <Project key={project.ui} mc={mc} project={project}></Project>)}
                <div className="project">
                    <p><ff.Link mc={mc} href="/new/">create a new project</ff.Link></p>
                </div>
            </div>
        </div>
    );
}


let newInit = async function(app, model, params) {
    return (app, model) => ff.clean(model).set("title", "").set("description", "");
}

let onNewView = function(app, model) {
    return async function(event) {
        let data = {
            title: model["title"],
            description: model["description"],
        }
        let response = await ff.post("/api/project/new/", data);
        if(response.status === 200) {
            let json = await response.json();
            let uid = json['uid']
            return await ff.redirect(app, ff.clean(model), "/project/" + uid + "/");
        } else {
            return (app, model) => ff.clean(model);
        }
    }
}

let NewView = function(model, mc) {
    ff.pk('NewView', model);
    return (
        <div id="container" className="new">
            <h1>lastho.pe</h1>
            <p>
                I want to start a new project entitled <ff.Input type="text" onChange={mc(ff.set("title"))} value={model["title"]} autoFocus={true} /> that will be about:
            </p>
            <textarea onChange={mc(ff.set('description'))} />
            <button onClick={mc(onNewView)}>start project</button>
        </div>
    );
}

let projectInit = async function(app, model, params) {
    let uid = params["uid"];
    ff.pk('project init', uid);
    let response = await ff.get("/api/project/" + uid + "/");
    let json = await response.json();
    return (app, model) => ff.Immutable(json).set('query', '');
}

let Query = function({mc, item}) {
    return <div className="item query" key={item.uid}>{item.value}</div>;
}

let Hit = function({mc, item}) {
    return (
        <a href="/" className="item hit">
            <p className="title">{item.value.title}</p>
            <p className="url">{item.value.url}</p>
            <p className="content">{item.value.content}</p>
        </a>
    );
}

let ItemToView = {
    query: Query,
    reply: Hit,
}

let onQuery = function(app, model) {
    return async function(event) {
        let uid = model["uid"];
        let query = model["query"];
        await ff.post("/api/project/" + uid + "/", {query: query});
        // refresh the lazy way
        return await ff.redirect(app, model, "/project/" + uid + "/", false);
    }
}

let ProjectView = function(model, mc) {
    ff.pk('project view', model);
    return (
        <div id="container" className="project">
            <h1>lastho.pe - project-name</h1>
            {model["items"].map(item => ItemToView[item.type]({mc: mc, item: item}))}
            <div className="form">
                <ff.Input type="text" autoFocus={true} value={model['query']} onChange={mc(ff.set('query'))} />
                <button onClick={mc(onQuery)}>query</button>
            </div>
        </div>
    );
}

let router = new ff.Router();
router.append('/', indexInit, IndexView);
router.append('/new/', newInit, NewView);
router.append('/project/{uid}/', projectInit, ProjectView);

ff.createApp(router);


// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister();

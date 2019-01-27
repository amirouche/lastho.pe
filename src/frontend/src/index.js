import React from 'react';
// import ReactDOM from 'react-dom';
import * as serviceWorker from './serviceWorker';

import './index.css';
import ff from './ff.js';


let projects = [
    {
        key: "infine",
        title: "infine.js",
        description: "Lazy Tree Grid Widget that can be queried.",
    },
    {
        key: "lasthope",
        title: "lastho.pe",
        description: "Personal Knowledge Base, the memex meets hypertext era.",
    }
]


let Project = function({mc, project}) {
    ff.pk(project.key);
    return (
        <div className="project">
            <h2><a href={"/project/" + project.key + "/"} >{project.title}</a></h2>
            <p>{project.description}</p>
        </div>
    )
}


let IndexView = function(model, mc) {
    return (
        <div id="container" className="index">
            <h1>lastho.pe</h1>
            <div>
                {projects.map(project => <Project key={project.key} mc={mc} project={project}></Project>)}
                <div className="project">
                    <p><ff.Link mc={mc} href="/new/">create a new project</ff.Link></p>
                </div>
            </div>
        </div>
    );
}


let NewView = function(model, mc) {
    return (
        <div id="container" className="new">
            <h1>lastho.pe</h1>
            <p>
                I want to start a new project entitled <ff.Input mc={mc} type="text" onChange={mc(ff.set("title"))} /> that will be about:
            </p>
            <textarea/>
            <button>start project</button>
        </div>
    );
}

let projectInit = async function(app, model, params) {
    ff.pk('project init', app, model, params);
    return (app, model) => ff.clean(model);
}

let convo = [
    {
        key: 1,
        type: "description",
        value: "The initial description of the project by the user"
    },
    {
        key: 12,
        type: "input",
        value: "google lastho.pe",
    },
    {
        key: 13,
        type: "hit",
        title: "lastho.pe - memex meets the hypertext era",
        description: "Productivity tool to improve (re)search experience. Organize your activity around project, keep track of progress and outline the solution.",
        url: "https://lastho.pe",
    },
    {
        key: 14,
        type: "hit",
        title: "lastho.pe - memex meets the hypertext era",
        description: "Productivity tool to improve (re)search experience. Organize your activity around project, keep track of progress and outline the solution.",
        url: "https://lastho.pe",
    },
    {
        key: 15,
        type: "hit",
        title: "lastho.pe - memex meets the hypertext era",
        description: "Productivity tool to improve (re)search experience. Organize your activity around project, keep track of progress and outline the solution.",
        url: "https://lastho.pe",
    },
    {
        key: 16,
        type: "hit",
        title: "lastho.pe - memex meets the hypertext era",
        description: "Productivity tool to improve (re)search experience. Organize your activity around project, keep track of progress and outline the solution.",
        url: "https://lastho.pe",
    },
    {
        key: 161,
        type: "hit",
        title: "lastho.pe - memex meets the hypertext era",
        description: "Productivity tool to improve (re)search experience. Organize your activity around project, keep track of progress and outline the solution.",
        url: "https://lastho.pe",
    },
    {
        key: 162,
        type: "hit",
        title: "lastho.pe - memex meets the hypertext era",
        description: "Productivity tool to improve (re)search experience. Organize your activity around project, keep track of progress and outline the solution.",
        url: "https://lastho.pe",
    },
    {
        key: 163,
        type: "hit",
        title: "lastho.pe - memex meets the hypertext era",
        description: "Productivity tool to improve (re)search experience. Organize your activity around project, keep track of progress and outline the solution.",
        url: "https://lastho.pe",
    },

]

let Description = function({mc, item}) {
    return <div className="item description">{item.value}</div>;
}

let Input = function({mc, item}) {
    return <div className="item input">{item.value}</div>;
}

let Hit = function({mc, item}) {
    return (
        <a href="/" className="item hit">
            <p className="title">{item.title}</p>
            <p className="url">{item.url}</p>
            <p className="description">{item.description}</p>
        </a>
    );
}

let ItemToView = {
    description: Description,
    input: Input,
    hit: Hit,
}

let ProjectView = function(model, mc) {
    return (
        <div id="container" className="project">
            <h1>lastho.pe - project-name</h1>
            {convo.map(item => ItemToView[item.type]({mc: mc, item: item}))}
            <div class="form">
                <ff.Input type="text" autoFocus={true} onChange={mc(ff.set('query'))} />
                <button>query</button>
            </div>
        </div>
    );
}

let router = new ff.Router();
router.append('/', ff.routeClean, IndexView);
router.append('/new/', ff.routeClean, NewView);
router.append('/project/{name}/', projectInit, ProjectView);

ff.createApp(router);


// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister();

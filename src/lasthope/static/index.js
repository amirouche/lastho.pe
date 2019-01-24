const h = require('react-hyperscript');
const React = require('react');
const ReactDOM = require('react-dom');
const hh = require('hyperscript-helpers')(h);


class Input extends React.Component {
    // ref https://github.com/facebook/react/issues/955

    constructor(props, ...args) {
        super(props, ...args);
        this.state = { value: props.value };
    }

    componentWillReceiveProps(nextProps) {
        if (this.state.value !== nextProps.value) {
            this.setState({ value: nextProps.value });
        }
    }

    onChange(event) {
        event.persist();
        this.setState({ value: event.target.value }, () => this.props.onChange(event));
    }

    render() {
        return (<input {...this.props} {...this.state} onChange={this.onChange.bind(this)} />);
    }
}


export default {h, ReactDOM, Input};

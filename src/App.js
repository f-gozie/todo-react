import React, { Component } from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom';

// Components
import Todos from './components/Todos';
import AddTodo from './components/AddTodo';
import Header from './components/layout/Header';
import About from './components/pages/About';

// Third Party
// import {v4 as uuidv4 } from 'uuid';
import axios from 'axios';

// Styles
import './App.css';

class App extends Component {

	state = {
		todos: []
    }
    
    componentDidMount () {
        axios.get("https://jsonplaceholder.typicode.com/todos?_limit=10").then(res => this.setState({ todos: res.data }));
    }
    
    // Toggle complete state
    markComplete = (id) => {
            this.setState({
                todos: this.state.todos.map(todo => {
                    if(todo.id === id) {
                        todo.completed = !todo.completed;
                    }
                    return todo;
                })
            });
        }

    // Delete current list item
    deleteItem = (id) => {
        axios.delete(`https://jsonplaceholder.typicode.com/todos/${id}`).then(
            this.setState({ 
                todos: [...this.state.todos.filter(todo => todo.id !== id)]
            })
        )
        this.setState({
            todos: [...this.state.todos.filter(todo => todo.id !== id)]
        });
    }

    // Add a new list item
    addItem = (title) => {
        axios.post('https://jsonplaceholder.typicode.com/todos', {title, completed: false}).then(
            res => this.setState({
                todos: [...this.state.todos, res.data]
            })
        )
    }
    
	render() {
		return (
            <Router>
                <div className="App">
                    <div className='container'>
                        <Header />
                        <Route exact path="/" render={ props => (
                            <React.Fragment>
                                <AddTodo addItem={this.addItem}/>
                                <Todos todos={this.state.todos} markComplete={this.markComplete} deleteItem={this.deleteItem}/>
                            </React.Fragment>
                        )} />  
                        <Route path="/about" component={About} />
                    </div>
                </div>
            </Router>
		);
	}
}

export default App;

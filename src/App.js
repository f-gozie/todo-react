import React, { Component } from 'react';
import Todos from './components/Todos';
import AddTodo from './components/AddTodo';
import Header from './components/layout/Header';
import './App.css';

class App extends Component {

	state = {
		todos: [
			{
				id: 1,
				title: "Take out the trash",
				completed: false,
			},
			{
				id: 2,
				title: "Push committed changes",
				completed: false,
			},
			{
				id: 3,
				title: "Populate DB using script",
				completed: false,
			}
		]
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
        this.setState({
            todos: [...this.state.todos.filter(todo => todo.id !== id)]
        });
    }

    // Add a new list item
    addItem = (title) => {
        const itemVar = {
            id: 4,
            title,
            completed: false
        }
        this.setState({todos: [...this.state.todos, itemVar]});
    }
    
	render() {
		return (
			<div className="App">
                <div className='container'>
                    <Header />
                    <AddTodo addItem={this.addItem}/>
                    <Todos todos={this.state.todos} markComplete={this.markComplete} deleteItem={this.deleteItem}/>
                </div>
			</div>
		);
	}
}

export default App;

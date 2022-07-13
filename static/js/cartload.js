const updateBtn = document.getElementsByClassName('update-cart');
for (let i = 0; i < updateBtn.length; i++) {
	updateBtn[i].addEventListener('click', function(){
		const productId = this.dataset.product;
		const action = this.dataset.action;
		const val = document.getElementsByClassName('quantity');
		let value = parseInt(val[i].value)
		console.log('productId:', productId, 'Action:', action, 'Value', value,)
		updateUserOrder(productId, action, value)
})
}

//this is for adding quantity
const AddBtn = document.getElementsByClassName('addQuantity')
for (let i = 0; i < AddBtn.length; i++) {
	AddBtn[i].addEventListener('click', function(){
		let add = document.getElementsByClassName('quantity');
		let value = parseInt(add[i].value)
		if (value<100) {
			value++
			add[i].value = value;
		}else {
			console.log('value must not be greater than 100')
			add[i].value = value
		}
	})
}



//this is for reducing quantity
const RedBtn = document.getElementsByClassName('reduceQuantity')
for (let i = 0; i < RedBtn.length; i++) {
	RedBtn[i].addEventListener('click', function(){
		console.log('clicked-');
		let minus = document.getElementsByClassName('quantity');
		let value = parseInt(minus[i].value)
		if (value>1){
			value--
			minus[i].value = value;
		}else {
			console.log('value must be greater or equal to 1')
			minus[i].value = value
		}


	})
}


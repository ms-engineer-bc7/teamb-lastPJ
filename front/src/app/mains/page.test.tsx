import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Home2 from './page';

describe('Home2', () => {
  test('renders input field and button', () => {
    render(<Home2 />);
    
    const inputElement = screen.getByPlaceholderText('最寄り駅か住所を入力してください');
    expect(inputElement).toBeInTheDocument();
    
    const buttonElement = screen.getByText('おすすめの駅を探す');
    expect(buttonElement).toBeInTheDocument();
  });

  test('updates input value on change', () => {
    render(<Home2 />);
    
    const inputElement = screen.getByPlaceholderText('最寄り駅か住所を入力してください');
    fireEvent.change(inputElement, { target: { value: '新宿' } });
    
    expect(inputElement).toHaveValue('新宿');
  });

  test('displays error message when input is empty and button is clicked', () => {
    render(<Home2 />);
    
    const buttonElement = screen.getByText('おすすめの駅を探す');
    fireEvent.click(buttonElement);
    
    const errorMessage = screen.getByText('駅名を入力してください');
    expect(errorMessage).toBeInTheDocument();
  });

  
});
use copypasta::{ClipboardContext, ClipboardProvider};
use crossterm::{
    event::{DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use std::{io, thread, time::Duration};
use tui::{
    backend::CrosstermBackend,
    layout::{Constraint, Layout},
    style::{Color, Modifier, Style},
    text::{Span, Spans},
    widgets::{Block, Borders, Cell, List, ListItem, ListState, Row, Table},
    Terminal,
};

fn challenges_table<'a>() -> Table<'a> {
    Table::new(vec![
        Row::new(vec![
            Cell::from("challenge_1").style(Style::default().fg(Color::Red)),
            Cell::from("10"),
            Cell::from("4"),
            Cell::from("10"),
            Cell::from("50"),
            Cell::from("100"),
            Cell::from("4"),
            Cell::from("2").style(Style::default().fg(Color::Green)),
            Cell::from("1000").style(Style::default().fg(Color::Red)),
        ]),
        Row::new(vec![
            Cell::from("da_challz").style(Style::default().fg(Color::Green)),
            Cell::from("13"),
            Cell::from("4"),
            Cell::from("12"),
            Cell::from("12"),
            Cell::from("120"),
            Cell::from("6"),
            Cell::from("10").style(Style::default().fg(Color::Green)),
            Cell::from("100").style(Style::default().fg(Color::Red)),
        ]),
        Row::new(vec![
            Cell::from("another_chall").style(Style::default().fg(Color::Yellow)),
            Cell::from("10"),
            Cell::from("4"),
            Cell::from("10"),
            Cell::from("50"),
            Cell::from("100"),
            Cell::from("4"),
            Cell::from("2").style(Style::default().fg(Color::Green)),
            Cell::from("1000").style(Style::default().fg(Color::Red)),
        ]),
        Row::new(vec![
            Cell::from("cool_chall").style(Style::default().fg(Color::Yellow)),
            Cell::from("10"),
            Cell::from("4"),
            Cell::from("10"),
            Cell::from("50"),
            Cell::from("100"),
            Cell::from("4"),
            Cell::from("2").style(Style::default().fg(Color::Green)),
            Cell::from("1000").style(Style::default().fg(Color::Red)),
        ]),
        Row::new(vec![
            Cell::from("hard_chall").style(Style::default().fg(Color::Yellow)),
            Cell::from("10"),
            Cell::from("4"),
            Cell::from("10"),
            Cell::from("50"),
            Cell::from("100"),
            Cell::from("4"),
            Cell::from("2").style(Style::default().fg(Color::Green)),
            Cell::from("1000").style(Style::default().fg(Color::Red)),
        ]),
    ])
    // You can set the style of the entire Table.
    .style(Style::default().fg(Color::White))
    // It has an optional header, which is simply a Row always visible at the top.
    .header(
        Row::new(vec![
            "Challenge",
            "Submitted",
            "Cancelled",
            "Building",
            "BuildOk",
            "BuildFailed",
            "Running",
            "RunSolved",
            "RunFailed",
        ])
        .style(Style::default().fg(Color::Yellow))
        // If you want some space between the header and the rest of the rows, you can always
        // specify some margin at the bottom.
        .bottom_margin(1),
    )
    // As any other widget, a Table can be wrapped in a Block.
    .block(Block::default().title("Challenges").borders(Borders::ALL))
    // Columns widths are constrained in the same way as Layout...
    .widths(&[
        Constraint::Min(14),
        Constraint::Min(14),
        Constraint::Min(14),
        Constraint::Min(14),
        Constraint::Min(14),
        Constraint::Min(14),
        Constraint::Min(14),
        Constraint::Min(14),
        Constraint::Min(14),
    ])
    // ...and they can be separated by a fixed spacing.
    .column_spacing(1)
    // If you wish to highlight a row in any specific way when it is selected...
    .highlight_style(Style::default().add_modifier(Modifier::BOLD))
    // ...and potentially show a symbol in front of the selection.
    .highlight_symbol(">>")
}

fn format_submission<'a>(
    exploit_id: &'a str,
    challenge: &'a str,
    team: &'a str,
    datetime: &'a str,
) -> ListItem<'a> {
    let style_exploit = Style::default().fg(Color::White);
    let style_team = Style::default()
        .fg(Color::Yellow)
        .add_modifier(Modifier::BOLD);
    let style_challenge = Style::default().fg(Color::LightBlue);
    let style_datetime = Style::default()
        .fg(Color::LightRed)
        .add_modifier(Modifier::ITALIC);

    let content = Spans::from(vec![
        Span::styled(exploit_id, style_exploit),
        Span::from(" "),
        Span::styled(datetime, style_datetime),
        Span::from(" "),
        Span::styled(challenge, style_challenge),
        Span::from(" "),
        Span::styled(team, style_team),
    ]);
    ListItem::new(content)
}

fn format_building<'a>(exploit_id: &'a str, challenge: &'a str, team: &'a str) -> ListItem<'a> {
    let style_exploit = Style::default().fg(Color::White);
    let style_team = Style::default()
        .fg(Color::Yellow)
        .add_modifier(Modifier::BOLD);
    let style_challenge = Style::default().fg(Color::LightBlue);

    let content = Spans::from(vec![
        Span::styled(exploit_id, style_exploit),
        Span::from(" "),
        Span::styled(challenge, style_challenge),
        Span::from(" "),
        Span::styled(team, style_team),
    ]);
    ListItem::new(content)
}

fn format_built<'a>(
    exploit_id: &'a str,
    challenge: &'a str,
    team: &'a str,
    ok: bool,
) -> ListItem<'a> {
    let style_exploit = Style::default().fg(Color::White);
    let style_team = Style::default()
        .fg(Color::Yellow)
        .add_modifier(Modifier::BOLD);
    let style_challenge = Style::default().fg(Color::LightBlue);
    let style_ok = Style::default()
        .fg(Color::Green)
        .add_modifier(Modifier::BOLD);
    let style_fail = Style::default().fg(Color::Red).add_modifier(Modifier::BOLD);

    let content = Spans::from(vec![
        Span::styled(exploit_id, style_exploit),
        Span::from(" "),
        Span::styled(challenge, style_challenge),
        Span::from(" "),
        Span::styled(team, style_team),
        Span::from(" "),
        if ok {
            Span::styled("BuildOk", style_ok)
        } else {
            Span::styled("BuildFailed", style_fail)
        },
    ]);
    ListItem::new(content)
}

fn format_running<'a>(exploit_id: &'a str, challenge: &'a str, team: &'a str) -> ListItem<'a> {
    let style_exploit = Style::default().fg(Color::White);
    let style_team = Style::default()
        .fg(Color::Yellow)
        .add_modifier(Modifier::BOLD);
    let style_challenge = Style::default().fg(Color::LightBlue);

    let content = Spans::from(vec![
        Span::styled(exploit_id, style_exploit),
        Span::from(" "),
        Span::styled(challenge, style_challenge),
        Span::from(" "),
        Span::styled(team, style_team),
    ]);
    ListItem::new(content)
}

fn format_run<'a>(
    exploit_id: &'a str,
    challenge: &'a str,
    team: &'a str,
    ok: bool,
) -> ListItem<'a> {
    let style_exploit = Style::default().fg(Color::White);
    let style_team = Style::default()
        .fg(Color::Yellow)
        .add_modifier(Modifier::BOLD);
    let style_challenge = Style::default().fg(Color::LightBlue);
    let style_ok = Style::default()
        .fg(Color::Green)
        .add_modifier(Modifier::BOLD);
    let style_fail = Style::default().fg(Color::Red).add_modifier(Modifier::BOLD);

    let content = Spans::from(vec![
        Span::styled(exploit_id, style_exploit),
        Span::from(" "),
        Span::styled(challenge, style_challenge),
        Span::from(" "),
        Span::styled(team, style_team),
        Span::from(" "),
        if ok {
            Span::styled("RunSolved", style_ok)
        } else {
            Span::styled("RunFailed", style_fail)
        },
    ]);
    ListItem::new(content)
}

fn submission_list<'a>() -> List<'a> {
    let items = [
        format_submission(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            "2023-04-13 13:37:00",
        ),
        format_submission(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            "2023-04-13 13:37:00",
        ),
        format_submission(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            "2023-04-13 13:37:00",
        ),
    ];
    List::new(items)
        .block(
            Block::default()
                .title("Recent submissions")
                .borders(Borders::ALL),
        )
        .style(Style::default().fg(Color::White))
        .highlight_style(Style::default().add_modifier(Modifier::ITALIC))
        .highlight_symbol(">>")
}

fn building_list<'a>() -> List<'a> {
    let items = [
        format_building("1111-111111-1111-1111-111111", "TestChallenge", "NorseCode"),
        format_building("1111-111111-1111-1111-111111", "TestChallenge", "NorseCode"),
        format_building("1111-111111-1111-1111-111111", "TestChallenge", "NorseCode"),
        format_building("1111-111111-1111-1111-111111", "TestChallenge", "NorseCode"),
        format_building("1111-111111-1111-1111-111111", "TestChallenge", "NorseCode"),
    ];
    List::new(items)
        .block(
            Block::default()
                .title("Currently building")
                .borders(Borders::ALL),
        )
        .style(Style::default().fg(Color::White))
        .highlight_style(Style::default().add_modifier(Modifier::ITALIC))
        .highlight_symbol(">>")
}

fn built_list<'a>() -> List<'a> {
    let items = [
        format_built(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            true,
        ),
        format_built(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            true,
        ),
        format_built(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            false,
        ),
        format_built(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            false,
        ),
        format_built(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            false,
        ),
        format_built(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            false,
        ),
        format_built(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            false,
        ),
        format_built(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            true,
        ),
        format_built(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            true,
        ),
        format_built(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            true,
        ),
    ];
    List::new(items)
        .block(
            Block::default()
                .title("Recent builds")
                .borders(Borders::ALL),
        )
        .style(Style::default().fg(Color::White))
        .highlight_style(Style::default().add_modifier(Modifier::ITALIC))
        .highlight_symbol(">>")
}

fn running_list<'a>() -> List<'a> {
    let items = [
        format_running(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "DragonSector",
        ),
        format_running("1111-111111-1111-1111-111111", "TestChallenge", "P4"),
        format_running("1111-111111-1111-1111-111111", "TestChallenge", "SomeTeam"),
        format_running("1111-111111-1111-1111-111111", "TestChallenge", "NorseCode"),
        format_running("1111-111111-1111-1111-111111", "TestChallenge", "CoolTeam"),
    ];
    List::new(items)
        .block(
            Block::default()
                .title("Currently running")
                .borders(Borders::ALL),
        )
        .style(Style::default().fg(Color::White))
        .highlight_style(Style::default().add_modifier(Modifier::ITALIC))
        .highlight_symbol(">>")
}

fn run_list<'a>() -> List<'a> {
    let items = [
        format_run(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            true,
        ),
        format_run(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "Samurai",
            false,
        ),
        format_run(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "Alles",
            true,
        ),
        format_run(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "ATeam",
            false,
        ),
        format_run(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "SomeTeam",
            true,
        ),
        format_run(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            false,
        ),
        format_run(
            "1111-111111-1111-1111-111111",
            "TestChallenge",
            "NorseCode",
            true,
        ),
    ];
    List::new(items)
        .block(Block::default().title("Recent runs").borders(Borders::ALL))
        .style(Style::default().fg(Color::White))
        .highlight_style(Style::default().add_modifier(Modifier::ITALIC))
        .highlight_symbol(">>")
}

fn main() -> Result<(), io::Error> {
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let mut ctx = ClipboardContext::new().unwrap();
    ctx.set_contents("EXPLOIT ID GOES HERE".to_string())
        .unwrap();

    'mainloop: for i in 1..1000 {
        terminal.draw(|f| {
            let size = f.size();
            let block = Block::default()
                .title(format!("Block - {i}"))
                .borders(Borders::ALL);

            f.render_widget(block, size);
            let chunks = Layout::default()
                .margin(1)
                //.constraints([Constraint::Percentage(100)].as_ref())
                .constraints(
                    [
                        Constraint::Percentage(25),
                        Constraint::Percentage(25),
                        Constraint::Percentage(25),
                        Constraint::Percentage(25),
                    ]
                    .as_ref(),
                )
                .split(f.size());

            let runs_block = Layout::default()
                .direction(tui::layout::Direction::Horizontal)
                .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
                .split(chunks[3]);

            let builds_block = Layout::default()
                .direction(tui::layout::Direction::Horizontal)
                .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
                .split(chunks[2]);
            //.title("Exploit runs")
            //.borders(Borders::ALL);

            f.render_widget(challenges_table(), chunks[0]);

            f.render_widget(submission_list(), chunks[1]);

            f.render_widget(building_list(), builds_block[0]);
            f.render_widget(built_list(), builds_block[1]);

            let mut state = ListState::default();
            state.select(Some(100));

            //f.render_widget(run_block, chunks[3]);
            f.render_stateful_widget(running_list(), runs_block[0], &mut state);
            f.render_widget(run_list(), runs_block[1]);
        })?;

        while crossterm::event::poll(Duration::from_millis(0))? {
            if let Event::Key(event) = crossterm::event::read()? {
                if let KeyCode::Char('q') = event.code {
                    break 'mainloop;
                }
            }
        }

        thread::sleep(Duration::from_millis(1000));
    }

    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    Ok(())
}

// TODO: display table of challenges, color for status, number of exploits in each state in each column
// TODO: display list with first X and last Y solves for current challenge
// TODO: display list with last X failed exploits

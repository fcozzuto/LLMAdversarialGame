def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (sx, sy))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    adj8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def neighbors8(x, y):
        for dx, dy in adj8:
            if dx == 0 and dy == 0: 
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                yield nx, ny

    def dist(a, b): 
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    mode_aggressive = (int(observation.get("turn_index", 0)) % 4) < 2

    safe_frontier = set()
    for x, y in self_terr:
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in unclaimed:
                # safe if not adjacent to opponent territory
                if all((ax, ay) not in opp_terr for ax, ay in neighbors8(nx, ny)):
                    safe_frontier.add((nx, ny))

    opp_frontier = set()
    for x, y in opp_terr:
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in unclaimed:
                opp_frontier.add((nx, ny))

    targets = opp_frontier if mode_aggressive else safe_frontier
    if not targets:
        targets = (safe_frontier or opp_frontier or unclaimed)

    # Evaluate candidate moves with simple deterministic scoring
    best = [0, 0]
    best_score = -10**18
    for dx, dy in adj8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        cell = (nx, ny)

        gain = 0
        if cell in self_terr:
            gain += 1
        elif cell in unclaimed:
            gain += 6 if cell in targets else 2
        elif cell in opp_terr:
            gain += 4  # possible flip on entry

        # avoid stepping into immediate opponent influence when playing safe
        opp_influence = 0
        if any((ax, ay) in opp_terr for ax, ay in neighbors8(nx, ny)):
            opp_influence = 1

        # keep distance from opponent when safe; press when aggressive
        d_to_opp = dist((nx, ny), (px, py))
        press = -d_to_opp if mode_aggressive else d_to_opp

        score = gain + (2 if cell in targets else 0) + press - (3 if (not mode_aggressive and opp_influence) else 0)

        # tie-breaker: prefer staying if equal to reduce flip risk deterministically
        if score > best_score or (score == best_score and [dx, dy] == [0, 0]):
            best_score = score
            best = [dx, dy]

    # ensure integers in {-1,0,1}
    return [int(best[0]), int(best[1])]
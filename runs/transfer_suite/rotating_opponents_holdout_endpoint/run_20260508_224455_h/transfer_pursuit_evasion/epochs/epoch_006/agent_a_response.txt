def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("evade" in role) or ("escape" in role) or ("runner" in role)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def dist2(x, y): 
        dx = x - ox; dy = y - oy
        return dx * dx + dy * dy
    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and not blocked(nx, ny):
                c += 1
        return c
    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)
    best = None
    best_score = None
    # Deterministic tie-break: fixed move order via (score, tie_index)
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        mob = mobility(nx, ny)
        d = dist2(nx, ny)
        e = edge_dist(nx, ny)
        # Walls: evader wants to hug walls; pursuer wants to avoid being forced into corners.
        wall_term = (7 - e) if is_evader else (-e)
        # Robustness: avoid low-mobility moves.
        mob_term = mob if is_evader else mob * 0.25
        # Main objective: evade maximize distance, pursue minimize distance.
        main = d if is_evader else (-d)
        score = main + wall_term + mob_term
        # Tie-break prefers earlier move index deterministically.
        key = (score, -mob, -e, -d if is_evader else d, -i)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]
    return best_move
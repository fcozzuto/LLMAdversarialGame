def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Strategy: chase best resource when we're competitive; otherwise contest by maximizing
    # opponent distance to the resource they can reach first.
    best_score = None
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        cur_self = man(nx, ny, ox, oy)
        total = 0.0
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # If opponent can reach this resource first, prioritize denying it:
            # maximize (od - sd) after move (should be less favorable to opponent).
            rel = od - sd

            # Extra pressure for nearby high-value resources; also discourage moving into
            # positions that reduce our ability to keep contesting.
            denom = 1 + sd + od
            base = (rel * 50.0) / denom

            # If we're already as close or closer, reward progress more directly.
            if sd <= od:
                base += 30.0 / (1 + sd)

            # Slightly penalize positions that increase opponent's general mobility advantage.
            # (Uses distance between agents as a cheap proxy.)
            base -= 0.15 * cur_self / (1 + denom)

            total += base
        if best_score is None or total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
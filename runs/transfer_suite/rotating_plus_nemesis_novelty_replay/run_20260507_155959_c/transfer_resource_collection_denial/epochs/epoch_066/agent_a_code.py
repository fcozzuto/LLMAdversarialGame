def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) != (sx, sy) and inb(nx, ny) and (nx, ny) not in obs:
                valid_moves.append((dx, dy))
    valid_moves.append((0, 0))
    valid_moves = sorted(valid_moves)

    # Fallback: go to nearest in-bounds non-obstacle if no resources
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in valid_moves:
            nx, ny = sx + dx, sy + dy
            if best is None or (abs(nx - tx) + abs(ny - ty), abs(dx) + abs(dy), dx, dy) < best:
                best = (abs(nx - tx) + abs(ny - ty), abs(dx) + abs(dy), dx, dy)
        return [best[2], best[3]]

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def eval_pos(nx, ny):
        # Prefer positions that beat opponent on a reachable resource, and collect if possible.
        best = -10**9
        for rx, ry in res:
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # If we are on the resource next step, heavily prioritize.
            if self_d == 0:
                score = 10**6 + (opp_d * 0.01)
            else:
                # Higher when our distance advantage is larger.
                score = (opp_d - self_d) * 1000 - self_d * 2
            if score > best:
                best = score
        return best

    best = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        sc = eval_pos(nx, ny)
        cand = (sc, -abs(dx) - abs(dy), dx, dy)  # prefer higher score, then longer step, deterministic tie
        if best is None or cand > best:
            best = cand
    return [best[2], best[3]]
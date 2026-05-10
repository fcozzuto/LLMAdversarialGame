def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    scores = observation.get("scores") or {}
    self_name = observation.get("self_name", "agent_a")
    opp_name = observation.get("opponent_name", "agent_b")
    my_score = float(scores.get(self_name, 0.0) or 0.0)
    op_score = float(scores.get(opp_name, 0.0) or 0.0)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def is_edge_cell(c):
        x, y = c
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (x + dx, y + dy) in opp_terr:
                    return True
        return False

    aggressive = my_score < op_score
    targets = []
    for c in unclaimed:
        if c in self_terr or c in opp_terr:
            continue
        adj = is_edge_cell(c)
        if aggressive and adj:
            targets.append(c)
        else:
            targets.append(c)
    if not targets:
        # fallback: head toward opponent territory edge or opponent position
        targets = list(opp_terr) if opp_terr else [(ox, oy)]

    best = [0, 0]
    best_score = -1e18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # consider local safety
        safe = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and (tx, ty) in obstacles:
                    safe -= 0.7
        # territory pressure
        edge_bonus = 0
        if (nx, ny) in opp_terr:
            edge_bonus += 6.0
        if aggressive and (nx, ny) in self_terr:
            edge_bonus -= 0.5
        if not aggressive and (nx, ny) in opp_terr:
            edge_bonus += 2.0

        # choose best target proximity
        best_t = 1e18
        attack_edge = 0
        for t in targets[:24]:  # keep deterministic and fast
            d = man(nx, ny, t[0], t[1])
            if d < best_t:
                best_t = d
                attack_edge = (1.5 if aggressive and is_edge_cell(t) else 0.0) + (0.8 if (t in opp_terr) else 0.0)
        score = (-best_t) * (1.2 if aggressive else 1.0) + edge_bonus + attack_edge + safe
        if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = [dx, dy]
    return [int(best[0]), int(best[1])]
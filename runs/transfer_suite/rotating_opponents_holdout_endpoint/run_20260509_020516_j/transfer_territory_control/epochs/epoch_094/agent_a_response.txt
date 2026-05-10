def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    selfT, oppT, unclaimed = set(), set(), set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    opp_pos = observation.get("opponent_position") or (W - 1, H - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    # Target preference: frontier unclaimed adjacent to opponent territory, else nearest unclaimed, else toward opponent position.
    frontier = set()
    if oppT:
        for x, y in oppT:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                        frontier.add((nx, ny))

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = None
    if frontier:
        target = min(frontier, key=lambda t: (manh(t, (sx, sy)), t[1], t[0]))
    else:
        candidates = [c for c in unclaimed if c not in obstacles]
        if candidates:
            target = min(candidates, key=lambda t: (manh(t, (sx, sy)), t[1], t[0]))
        else:
            target = (ox, oy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        score = 0
        if cell in oppT:
            score += 1000
        elif cell in unclaimed:
            score += 120
        elif cell in selfT:
            score += 10
        else:
            score += 0
        # Prefer moves that reduce distance to target, and slightly reduce distance to opponent.
        score += 60 - 2 * manh(cell, target)
        score += 3 * (-(manh(cell, (ox, oy))))
        # Deterministic tie-break: prefer lower (dy, dx) order by using final comparison tuple.
        key = (score, -manh(cell, target), ny, nx)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    # If all candidate moves were invalid (e.g., surrounded by obstacles), stay still.
    return best_move if best is not None else [0, 0]
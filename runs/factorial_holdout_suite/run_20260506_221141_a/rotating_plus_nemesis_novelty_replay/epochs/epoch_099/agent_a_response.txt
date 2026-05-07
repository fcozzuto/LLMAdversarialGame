def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    sx, sy = to_xy(observation.get("self_position", [0, 0]))
    ox, oy = to_xy(observation.get("opponent_position", [0, 0]))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh:
            obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_race_value(px, py):
        best_key = None
        for rx, ry in resources:
            sd = manh(px, py, rx, ry)
            od = manh(ox, oy, rx, ry)
            gap = od - sd  # positive => we can arrive sooner
            # prefer greater gap, then sooner for us, then deterministic coordinate tie-break
            key = (gap, -sd, -ry, -rx)
            if best_key is None or key > best_key:
                best_key = key
        return best_key[0], best_key

    # One-step lookahead over 9 moves to counter resource_denier
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < gw and 0 <= ny < gh):
                continue
            if (nx, ny) in obstacles:
                continue
            moves.append((dx, dy))

    if not moves:
        return [0, 0]

    cur_gap, _ = best_race_value(sx, sy)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        gap, key = best_race_value(nx, ny)
        # Make meaningful switches: prioritize improved race; if tied, move that heads towards target.
        # Slightly penalize lingering when already capable.
        bonus = 0
        if gap > cur_gap:
            bonus += 1000
        elif gap == cur_gap:
            # closer to currently best target (encoded in key)
            bonus += 10
        if dx == 0 and dy == 0:
            bonus -= 1
        # Deterministic final ordering via dx,dy and current best_key
        tie_key = (gap, key[1], key[2], key[3], bonus, -dx, -dy)
        if best is None or tie_key > best[0]:
            best = (tie_key, dx, dy)

    return [int(best[1]), int(best[2])]
def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources") or [])]
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    turns_remaining = int(observation.get("turns_remaining", 0))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = dist8(sx, sy, rx, ry)
        do = dist8(ox, oy, rx, ry)
        earlier = 1 if ds <= do else 0
        row_pen = 0
        if ry == oy:
            row_pen = 3
        elif abs(ry - oy) == 1:
            row_pen = 1
        # Earlier capture and opponent delay; time pressure increases near endgame
        time_boost = max(0, (turns_remaining // 6) - ds)
        score = (earlier * 1000) + (do - ds) * 10 - row_pen * 3 + time_boost - ds
        if best is None or score > best[0]:
            best = (score, rx, ry, ds, do)

    if best is None:
        return [0, 0]

    _, tx, ty, _, _ = best
    dx0, dy0 = tx - sx, ty - sy
    step_options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            step_options.append((dx, dy, nx, ny))
    if not step_options:
        return [0, 0]

    # Prefer moves that reduce distance to target; also avoid stepping onto opponent-favored rows
    opp_row_pen = 0
    best_move = None
    cur_dist = dist8(sx, sy, tx, ty)
    for dx, dy, nx, ny in step_options:
        nd = dist8(nx, ny, tx, ty)
        move_pen = 0
        if ny == oy:
            move_pen += 2
        elif abs(ny - oy) == 1:
            move_pen += 1
        # Slightly encourage progress when behind, discourage when equal/behind threat
        progress = cur_dist - nd
        threat = dist8(ox, oy, tx, ty) - dist8(ox, oy, nx, ny)
        sc = progress * 50 - nd - move_pen * 3 + threat * 2
        if best_move is None or sc > best_move[0]:
            best_move = (sc, dx, dy)

    return [int(best_move[1]), int(best_move[2])]
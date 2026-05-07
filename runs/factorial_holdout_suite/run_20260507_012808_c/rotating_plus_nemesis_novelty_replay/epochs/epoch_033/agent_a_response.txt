def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        target = (ox, oy)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            d = abs(cx - sx) + abs(cy - sy)
            # Prefer moving away from opponent to avoid their sweep pressure
            s = d - 0.1 * (abs(cx - ox) + abs(cy - oy))
            if best is None or s < best[0]:
                best = (s, cx, cy)
        if best is not None:
            target = (best[1], best[2])
        tx, ty = target
    else:
        best = None
        for rx, ry in resources:
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            # Main: arrive earlier; secondary: closer to us; tertiary: reduce opponent interference
            s = ds - 1.25 * do
            if best is None or s < best[0]:
                best = (s, rx, ry)
        tx, ty = best[1], best[2]

    # Choose next step among valid deltas; prefer reducing distance with diagonal if possible
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx = sx + dx; ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        opp_dist = abs(tx - ox) + abs(ty - oy)
        # Encourage diagonal when it helps, and avoid stepping into "relay" squares that keep us behind
        step_val = dist - 0.08 * (opp_dist) + (0.03 if (dx == 0 or dy == 0) else 0.0)
        if best_val is None or step_val < best_val:
            best_val = step_val
            best_move = (dx, dy)

    dx, dy = best_move
    dx = int(dx); dy = int(dy)
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [dx, dy]
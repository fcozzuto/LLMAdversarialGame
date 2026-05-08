def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    if (sx, sy) in obs:
        return [0, 0]
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    # Pick target we can contest best: prioritize leading resources, else nearest we can reach fastest.
    best = None
    best_val = None
    for rx, ry in res:
        dself = man((sx, sy), (rx, ry))
        dopp = man((ox, oy), (rx, ry))
        lead = dopp - dself  # positive => we are closer
        # Value: strongly prefer positive lead; among them prefer smaller self distance and larger lead.
        val = (1 if lead > 0 else 0, lead, -dself, -abs(rx - sx) - abs(ry - sy))
        if best_val is None or val > best_val:
            best_val = val
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # Evaluate moves by improving our contest for the chosen target; slight bias to reduce opponent progress to the target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dnew = man((nx, ny), (tx, ty))
        lead_new = man((ox, oy), (tx, ty)) - dnew
        # Also add small check: if we are behind, try to reduce lead deficit more than just distance.
        lead_score = lead_new if lead_new > 0 else -abs(lead_new)
        score = (1 if lead_new > 0 else 0, lead_score, -dnew, -(abs(nx - tx) + abs(ny - ty)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
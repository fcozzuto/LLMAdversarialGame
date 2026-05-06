def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def edge_pen(nx, ny):
        return 1 if nx in (0, w - 1) or ny in (0, h - 1) else 0

    best = None  # (score_tuple, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Choose the resource where we gain most relative positioning vs opponent.
        best_adv = None
        best_our_d = None
        for rx, ry in resources:
            our_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            adv = opp_d - our_d
            if best_adv is None or adv > best_adv or (adv == best_adv and our_d < best_our_d):
                best_adv, best_our_d = adv, our_d

        opp_close = abs(nx - ox) + abs(ny - oy)
        # Prefer staying interior; prefer big advantage; then closer to target; then slightly farther from opponent.
        score = (-best_adv, edge_pen(nx, ny), best_our_d, -opp_close)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]] if best else [0, 0]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(dx, dy):
        nx, ny = sx + dx, sy + dy
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Also softly prefer staying on the same "half" as the opponent to reduce escape routes.
    def side_bias(nx, ny):
        # corners: (0,0),(w-1,h-1) etc; choose the corner closer to opponent and bias away from it.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        # pick opponent-closest corner deterministically
        bestc = min(range(4), key=lambda i: dist2(ox, oy, corners[i][0], corners[i][1]))
        cx, cy = corners[bestc]
        # prefer moves that get closer to opponent while not moving farther from that corner too much
        return dist2(nx, ny, cx, cy)

    best = None
    best_score = None
    for dx, dy in deltas:
        if not legal(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        d_to_opp = dist2(nx, ny, ox, oy)
        # tie-break: prefer reducing distance to opponent, then avoid stepping away from opponent's corner.
        score = (d_to_opp, side_bias(nx, ny), abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)
    resources = observation.get("resources") or []
    inb = lambda x, y: 0 <= x < gw and 0 <= y < gh

    # Choose a target: nearest resource; otherwise center.
    if resources:
        best = None
        bd = 10**9
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in obs:
                continue
            d = abs(rx - sx) + abs(ry - sy)
            if d < bd:
                bd, best = d, (rx, ry)
        tx, ty = best if best is not None else (gw // 2, gh // 2)
    else:
        tx, ty = (gw // 2, gh // 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestscore = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (dx == 0 and dy == 0) and len(resources) > 0:
            pass
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer moving closer to target; small bias to avoid opponent.
        score = (abs(tx - nx) + abs(ty - ny)) * 1000 + (abs(ox - nx) + abs(oy - ny))
        if score < bestscore:
            bestscore = score
            bestm = (dx, dy)
    return [bestm[0], bestm[1]]
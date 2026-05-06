def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    cur_opp_dists = [manh(ox, oy, rx, ry) for (rx, ry) in resources]
    cur_opp_nearest = min(cur_opp_dists) if cur_opp_dists else 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        total = 0.0
        # Prefer making myself closer to resources the opponent is likely to chase.
        for i, (rx, ry) in enumerate(resources):
            myd = manh(nx, ny, rx, ry)
            oppd = cur_opp_dists[i]
            lead = oppd - myd  # >0 means I'm closer
            # If opponent is already close to this resource, contest it.
            opp_close = 1.0 if oppd <= cur_opp_nearest else 0.0
            if myd == 0:
                total += 1000.0
            # Reward catching up; penalize falling further behind.
            if lead >= 0:
                total += (20.0 + 2.0 * opp_close) + 1.5 * lead - 0.1 * myd
            else:
                total += -8.0 - 1.0 * (-lead) - 0.3 * myd - 2.0 * opp_close

        key = (-total, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]
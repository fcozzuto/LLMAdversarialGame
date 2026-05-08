def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0
        best = -10**18
        for i, (rx, ry) in enumerate(resources):
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we arrive before opponent; otherwise head to closer ones.
            adv = opd - myd
            score = adv * 1000 - myd * 3 - i
            # Add small tie-break: if opponent is also close, reduce willingness to contest unless we're closer.
            if adv <= 0:
                score -= (opd - myd) * 2 + opd * 0.5
            if score > best:
                best = score
        cand.append((best, dx, dy))

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]
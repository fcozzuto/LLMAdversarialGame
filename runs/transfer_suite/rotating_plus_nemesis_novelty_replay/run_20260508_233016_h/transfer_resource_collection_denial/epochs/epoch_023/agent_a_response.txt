def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick among a small shortlist near me; score favors resources I'm likely to secure first.
    scored = []
    for (rx, ry) in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        diff = od - sd  # positive => I'm closer
        # Slightly prefer central-ish y to avoid predictable edge sweeps.
        center_bias = -0.05 * abs(ry - (h - 1) / 2)
        # If I'm not closer, still allow it but reduce priority.
        ahead = 2.0 if diff >= 0 else 0.6
        val = sd - ahead * max(0, diff) * 0.9 + center_bias
        scored.append((val, sd, rx, ry))
    scored.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    _, _, tx, ty = scored[0]

    # Greedy step toward target with tie-breaking.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_md = None
    cur_md = man(sx, sy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        md = man(nx, ny, tx, ty)
        # Prefer strictly improving; if not possible, prefer smallest increase; then prefer diagonal.
        improve = 1 if md < cur_md else (0 if md == cur_md else -1)
        diag = 1 if dx != 0 and dy != 0 else 0
        cand = (improve, -md, diag, dx, dy)
        if best is None or cand > best:
            best = cand
            best_md = md
    if best is not None:
        # Reconstruct move from tie-break order stored in cand.
        return [best[3], best[4]]

    return [0, 0]
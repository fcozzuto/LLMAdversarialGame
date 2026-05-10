def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    unclaimed = observation.get("unclaimed_cells", []) or []
    un = set((p[0], p[1]) for p in unclaimed)

    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opp_pos[0], opp_pos[1]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if not un and not opp:
        dx = 1 if x < w - 1 else (-1 if x > w - 1 else 0)
        dy = 1 if y < h - 1 else (-1 if y > h - 1 else 0)
        return [dx if inb(x + dx, y) else 0, dy if inb(x, y + dy) else 0]

    if un:
        # Deterministic "frontier": aim for the unclaimed cell with smallest (dist) but tie-break by max (surrounding unclaimed)
        def frontier_key(p):
            px, py = p
            d = abs(px - x) + abs(py - y)
            cnt = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    q = (px + ax, py + ay)
                    if q in un:
                        cnt += 1
            return (d, -cnt, px, py)
        tx, ty = min(un, key=frontier_key)
    else:
        tx, ty = min(opp, key=lambda p: (abs(p[0] - x) + abs(p[1] - y), p[0], p[1]))

    def step_dir(cx, cy, tx, ty):
        ddx = 0 if tx == cx else (1 if tx > cx else -1)
        ddy = 0 if ty == cy else (1 if ty > cy else -1)
        return ddx, ddy

    preferred_dx, preferred_dy = step_dir(x, y, tx, ty)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0.0
        if (nx, ny) in un:
            score += 6.0
        if (nx, ny) in opp:
            score += 4.5
        if (nx, ny) in selft:
            score += 1.2

        score += 2.0 * (-(abs(tx - nx) + abs(ty - ny)))  # closer to frontier
        score += -0.15 * (abs(ox - nx) + abs(oy - ny))   # don't chase opponent too directly
        score += 0.3 * ((dx == preferred_dx) + (dy == preferred_dy))

        # Deterministic tie-break
        tiebreak = (nx, ny)
        if score > best_score or (score == best_score and (best is None or tiebreak < (best[0] + best[1], best[0] + best[1]))):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]
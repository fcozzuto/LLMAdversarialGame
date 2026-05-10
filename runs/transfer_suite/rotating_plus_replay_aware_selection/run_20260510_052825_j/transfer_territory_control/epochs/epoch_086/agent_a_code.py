def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    opp_pos = observation.get("opponent_position", None)
    ox, oy = opp_pos if isinstance(opp_pos, (list, tuple)) and len(opp_pos) >= 2 else (None, None)

    resources = [tuple(p) for p in (observation.get("resources") or []) if p and len(p) >= 2]
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = resources if resources else unclaimed
    if targets:
        if ox is None:
            tx, ty = min(targets, key=lambda c: md((sx, sy), c))
        else:
            # Prefer getting away from opponent if close; else chase nearest target.
            if md((sx, sy), (ox, oy)) <= 2 and unclaimed:
                tx, ty = max(targets, key=lambda c: (md((ox, oy), c), -md((sx, sy), c)))
            else:
                tx, ty = min(targets, key=lambda c: (md((sx, sy), c), md((ox, oy), c) if ox is not None else 0))
    else:
        tx, ty = (w // 2, h // 2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = md((nx, ny), (tx, ty))
        if ox is not None:
            score += 0.1 * (max(0, 3 - md((nx, ny), (ox, oy))))  # mild penalty if too close
        cand = (score, abs(dx) + abs(dy))
        if best is None or cand < best[0]:
            best = (cand, [dx, dy])
    return best[1] if best is not None else [0, 0]
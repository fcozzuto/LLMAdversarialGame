def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 0), observation.get("grid_height", 0)
    if not (isinstance(w, int) and isinstance(h, int) and 0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ox, oy = observation.get("opponent_position", (sx, sy))

    unclaimed = observation.get("unclaimed_cells") or []
    use_unclaimed = bool(unclaimed)

    # Pre-pick a small set of target cells to keep deterministic and fast.
    targets = []
    if use_unclaimed:
        lim = 40 if len(unclaimed) > 40 else len(unclaimed)
        for i in range(lim):
            p = unclaimed[i]
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue

        score = 0
        d_opp = dist(nx, ny, ox, oy)
        if (nx, ny) == (ox, oy):
            score += 10**9
        score += 200 - 3 * d_opp

        if targets:
            md = 10**9
            # Only scan a small deterministic subset.
            for tx, ty in targets:
                d = dist(nx, ny, tx, ty)
                if d < md:
                    md = d
            score += 120 - 2 * md

        # Small deterministic tie-break: prefer moves that don't stay if equal score.
        if score > best[0] or (score == best[0] and (dx, dy) != (0, 0) and best[1] == 0 and best[2] == 0):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]
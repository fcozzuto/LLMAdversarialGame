def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        return max(abs(bx - ax), abs(by - ay))

    if not resources or all((rx, ry) in obstacles for rx, ry in resources):
        return [0, 0]

    best = [0, 0]
    best_score = -10**30
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        score = 0
        # Primary: pick resource where we can arrive no later than opponent.
        # Secondary: if none, choose move that reduces opponent lead and heads toward the nearest resource.
        best_beat = None
        best_any = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = dist(nsx, nsy, rx, ry)
            ot = dist(ox, oy, rx, ry)
            if best_any is None or st < best_any[0]:
                best_any = (st, ot, rx, ry)
            if st <= ot:
                if best_beat is None or (st, ot) < (best_beat[0], best_beat[1]):
                    best_beat = (st, ot, rx, ry)

        if best_beat is not None:
            st, ot, rx, ry = best_beat
            # Encourage winning earlier and, slightly, being closer to the target.
            score = (ot - st) * 1000 + (100 - st) + (w + h - dist(nsx, nsy, rx, ry))
        else:
            # Resource_denier: if we can't win any, minimize the best opponent lead and still move toward something.
            st, ot, rx, ry = best_any
            score = -(ot - st) * 800 + (100 - st)
            # Add small bias toward increasing distance from opponent while progressing.
            score += (dist(nsx, nsy, ox, oy) - dist(sx, sy, ox, oy)) * 5

        # Small deterministic tiebreak: prefer not moving vertically/horizontally first in a consistent order
        if score > best_score or (score == best_score and (mdx, mdy) > (best[0], best[1])):
            best_score = score
            best = [mdx, mdy]

    return [int(best[0]), int(best[1])]
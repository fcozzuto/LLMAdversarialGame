def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    opp_d = king_dist(sx, sy, ox, oy)
    center = (w - 1) / 2.0, (h - 1) / 2.0

    if not moves:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if resources:
            total = 0.0
            for rx, ry in resources:
                ds = king_dist(nx, ny, rx, ry)
                do = king_dist(ox, oy, rx, ry)
                # Prefer resources where we are closer than opponent after our move.
                # Secondary: if we aren't closer, reduce opponent's advantage.
                # Tertiary: avoid letting opponent reach very fast.
                if ds == 0:
                    val = 10000.0
                else:
                    val = 1.0 / (1 + ds)
                contest = (do - ds)  # positive favors us
                urgency = 1.0 / (1 + do)
                total += val * (200.0 + 20.0 * contest) + 30.0 * urgency * contest
            # Defensive term: if opponent is near, keep increasing their distance.
            total += (opp_d <= 2) * 50.0 * king_dist(nx, ny, ox, oy)
            # Small tie-breaker towards center to reduce dithering.
            total += -0.01 * king_dist(nx, ny, int(center[0] + 0.5), int(center[1] + 0.5))
        else:
            # No resources: move toward center while increasing distance from opponent.
            total = -king_dist(nx, ny, int(center[0] + 0.5), int(center[1] + 0.5))
            total += 0.5 * king_dist(nx, ny, ox, oy)

        if best_score is None or total > best_score:
            best_score = total
            best_move = (dx, dy)
        elif total == best_score:
            # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying.
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
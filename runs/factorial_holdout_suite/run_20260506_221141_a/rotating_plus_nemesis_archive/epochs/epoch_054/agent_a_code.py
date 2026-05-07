def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_mv = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my = (nx, ny)
        score = -10**9
        for t in resources:
            d_self = dist(my, t)
            d_opp = dist((ox, oy), t)

            # Favor resources we can get earlier; also slightly avoid being "too late".
            s = 100 * (d_opp - d_self) - d_self

            # If we land on the target this turn, strongly prefer.
            if my[0] == t[0] and my[1] == t[1]:
                s += 10000

            # Mild preference for moving along diagonals/hard-to-deny when close.
            s -= 0.2 * (abs(dx) + abs(dy))

            if s > score:
                score = s

        if best is None or score > best:
            best = score
            best_mv = [dx, dy]
        elif score == best:
            # Deterministic tie-break: prefer staying closer to center-left progression (min distance to left-top diagonal).
            pref = abs((w - 1 - nx) - (h - 1 - ny))
            pref0 = abs((w - 1 - best_mv[0] - sx) - (h - 1 - best_mv[1] - sy))
            if pref < pref0:
                best_mv = [dx, dy]

    return [int(best_mv[0]), int(best_mv[1])]
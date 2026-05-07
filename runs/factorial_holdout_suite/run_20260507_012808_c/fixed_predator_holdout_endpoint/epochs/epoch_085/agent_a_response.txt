def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    turns = int(observation.get("turns_remaining") or 0)

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        worst = None
        # We want a resource where we are at least as good as opponent (or better).
        for tx, ty in resources:
            sd = manh(nx, ny, tx, ty)
            od = manh(ox, oy, tx, ty)
            # Prefer hitting within remaining time, and prefer where we have advantage.
            time_bonus = 0
            if turns > 0:
                # If both can reach, prefer larger advantage; if only we can, huge.
                if sd <= turns and od <= turns:
                    time_bonus = 3 * (od - sd)
                elif sd <= turns and od > turns:
                    time_bonus = 100
                elif sd > turns and od <= turns:
                    time_bonus = -100
            val = (od - sd) * 10 + time_bonus - sd
            if worst is None or val > worst:
                worst = val

        # Deterministic tie-break: larger worst, then smaller self distance to its best target approximation.
        if best_val is None or worst > best_val or (worst == best_val and (dx, dy) < tuple(best_move)):
            best_val = worst
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
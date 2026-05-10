def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role) or ("hunter" in role) or (not evader)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    obstacles = list(blocked)

    def obstacle_cost(nx, ny):
        if not obstacles:
            return 0
        md = 10**9
        for x, y in obstacles:
            dd = dist2(nx, ny, x, y)
            if dd < md:
                md = dd
        # Stronger penalty for being adjacent; still smooth for diagonals.
        return 40.0 / (1.0 + md)

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        oc = obstacle_cost(nx, ny)

        if evader:
            # Maximize distance, but also keep away from obstacles and avoid moving into "opponent line"
            # by preferring changes that increase distance more.
            score = float(d) - oc * 1.1
        else:
            # Pursuer: minimize distance; prefer moves that approach while not hugging obstacles.
            score = -float(d) - oc * 0.8

        # Tie-break deterministically by move index
        key = (score, -((dx == 0) and (dy == 0)), -(dx * dx + dy * dy))
        # Normalize ordering so key comparisons stable: use move position as final deterministic tiebreaker
        idx = moves.index((dx, dy))
        key = (key[0], key[1], key[2], -idx)

        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]
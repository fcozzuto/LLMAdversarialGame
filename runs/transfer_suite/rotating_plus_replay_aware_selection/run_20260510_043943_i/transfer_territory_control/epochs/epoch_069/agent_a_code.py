def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                unclaimed.append((x, y))

    self_t = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))
    op_t = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            op_t.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []

    if unclaimed:
        # choose nearest unclaimed as main target
        tx, ty = min(unclaimed, key=lambda q: abs(q[0] - sx) + abs(q[1] - sy))
    else:
        # if no unclaimed, aim to approach opponent territory or just hold position
        tx, ty = ox, oy

    # small frontier term: prefer moves that land on/adjacent to opponent territory when it helps to reduce distance to target
    def frontier(x, y):
        best = 0
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in op_t:
                best += 1
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        md = abs(tx - nx) + abs(ty - ny)
        # prefer closer to target, strongly prefer stepping onto unclaimed, otherwise mild preference for expansion
        val = -md * 10

        if (nx, ny) in self_t:
            val -= 1  # avoid redundant steps
        if (nx, ny) in op_t:
            val += 6 + frontier(nx, ny) * 0.5  # flipping on entry is allowed
        if (nx, ny) in set(unclaimed):
            val += 50  # immediate gain

        # also prefer not to move away from opponent when no unclaimed exists
        if not unclaimed:
            val += -((abs(ox - nx) + abs(oy - ny)) * 0.5)

        # tie-break deterministically toward lexicographically smaller move
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
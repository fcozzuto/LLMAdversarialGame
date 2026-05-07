def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    res = resources
    res_set = set(res)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Prefer moves that make us strictly closer than opponent to some resource,
    # otherwise just get close to the best remaining resource.
    move_list = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_move = [0, 0]

    for dx, dy in move_list:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate best target from the hypothetical next position
        best_target = None
        best_selfd = None
        for rx, ry in res:
            selfd = manh(nx, ny, rx, ry)
            oppd = manh(ox, oy, rx, ry)
            # primary: gain (oppd - selfd), secondary: faster (selfd)
            gain = oppd - selfd
            # If we can arrive sooner (gain>0), strongly prefer; else still prefer high gain and closeness.
            score1 = 1000 if gain > 0 else 0
            score = (score1 + gain, -selfd, 0 if (nx, ny) in res_set else 1)
            if best_target is None or score > best_target:
                best_target = score
                best_selfd = selfd

        # Tie-break deterministically: prefer moves that land on a resource, then lexicographic move_list order
        landed = 0 if (nx, ny) in res_set else 1
        overall = (best_target, -landed, -abs(dx) - abs(dy))
        if best is None or overall > best:
            best = overall
            best_move = [dx, dy]

    return best_move
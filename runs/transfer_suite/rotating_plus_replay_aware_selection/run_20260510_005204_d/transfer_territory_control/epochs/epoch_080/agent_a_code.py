def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def norm_cell(p):
        if not p or len(p) < 2:
            return None
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            return (x, y)
        return None

    self_terr = set([c for c in (observation.get("self_territory") or []) if (c and len(c) >= 2) and (0 <= int(c[0]) < w and 0 <= int(c[1]) < h)])
    opp_terr = set([c for c in (observation.get("opponent_territory") or []) if (c and len(c) >= 2) and (0 <= int(c[0]) < w and 0 <= int(c[1]) < h)])
    unclaimed = set([c for c in (observation.get("unclaimed_cells") or []) if (c and len(c) >= 2) and (0 <= int(c[0]) < w and 0 <= int(c[1]) < h)])

    dirs8 = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    goals = []
    if self_terr:
        for (x, y) in self_terr:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    goals.append((nx, ny))
    if not goals:
        goals = list(unclaimed)

    if not goals:
        target = (w // 2, h // 2)
    else:
        # Prefer reachable expansion and staying away from the opponent for safer growth.
        target = min(goals, key=lambda g: (man((sx, sy), g), -man((ox, oy), g), g[0], g[1]))

    tx, ty = target
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    cand_moves = []
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Tie-break deterministically: closer to target, then farther from opponent.
        cand_moves.append((man((nx, ny), target), -man((nx, ny), (ox, oy)), (dx, dy)))
    if not cand_moves:
        return [0, 0]
    cand_moves.sort()
    dx, dy = cand_moves[0][2]
    return [int(dx), int(dy)]
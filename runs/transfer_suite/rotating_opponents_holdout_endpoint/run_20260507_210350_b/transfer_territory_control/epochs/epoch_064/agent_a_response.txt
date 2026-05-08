def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    resources = set((int(p[0]), int(p[1])) for p in (observation.get("resources") or []) if p and len(p) >= 2)

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def candidates_from_edges():
        edges = set()
        for ax, ay in oppT:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = ax + dx, ay + dy
                    if inside(nx, ny) and (nx, ny) not in oppT:
                        edges.add((nx, ny))
        usable = [c for c in edges if c in unclaimed or c in resources]
        return usable

    edge_targets = candidates_from_edges()
    if not edge_targets:
        targets = [p for p in unclaimed if p not in obstacles] + [p for p in resources if p not in obstacles]
        edge_targets = targets if targets else [(w // 2, h // 2)]

    # Choose a deterministic target: prioritize nearest edge target, tiebreak toward opponent.
    target = min(edge_targets, key=lambda t: (cheb((sx, sy), t), -cheb(t, (ox, oy)), t[1], t[0]))

    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        pos = (nx, ny)
        gain = 0.0
        if pos in oppT:
            gain += 60.0  # immediate flip pressure
        if pos in unclaimed:
            gain += 18.0
        if pos in resources:
            gain += 10.0
        if pos in selfT:
            gain -= 3.0  # avoid just expanding slow
        # Move toward target, but also don't drift away from opponent too much.
        dist_to_target = cheb((nx, ny), target)
        dist_to_opp = cheb((nx, ny), (ox, oy))
        move_score = gain + (20.0 / (1.0 + dist_to_target)) + (-0.8 * dist_to_target) + (-0.15 * dist_to_opp)
        moves.append(((dx, dy), move_score))

    if not moves:
        return [0, 0]
    best = max(moves, key=lambda item: (item[1], -item[0][0], -item[0][1]))
    return [int(best[0][0]), int(best[0][1])]
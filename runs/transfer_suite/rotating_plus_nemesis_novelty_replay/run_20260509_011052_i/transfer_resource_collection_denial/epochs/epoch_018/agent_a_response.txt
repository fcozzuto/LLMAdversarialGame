def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cd(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose a target resource deterministically: closest; if tie, prefer one more "away from opponent".
    target = res[0]
    best_td = cd((sx, sy), target)
    best_od = cd((ox, oy), target)
    for r in res[1:]:
        td = cd((sx, sy), r)
        od = cd((ox, oy), r)
        if td < best_td or (td == best_td and od > best_od) or (td == best_td and od == best_od and (r[0], r[1]) < (target[0], target[1])):
            target = r
            best_td, best_od = td, od

    # Evaluate one-step moves: greedily reduce distance to target, but avoid getting too close to opponent.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to_target = cd((nx, ny), target)
        d_from_opp = cd((nx, ny), (ox, oy))
        score = -d_to_target * 10 + d_from_opp  # primary: reach target; secondary: stay safer vs denier
        if (nx, ny) == target:
            score += 1000
        # Deterministic tie-break using lexicographic preference on deltas
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
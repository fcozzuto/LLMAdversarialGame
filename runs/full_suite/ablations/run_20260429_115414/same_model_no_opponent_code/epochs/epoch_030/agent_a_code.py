def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    if resources:
        # Choose a deterministic target: closest by dist2, tie by (x,y)
        target = min(resources, key=lambda r: (dist2(self_pos, r), r[1], r[0]))
        tx, ty = target
    else:
        # No resources: move toward center-ish to avoid getting trapped
        tx, ty = w // 2, h // 2

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        pos = (nx, ny)
        # Objective: approach target, also avoid allowing opponent to get closer too quickly.
        cur = dist2(pos, (tx, ty))
        opp = dist2(pos, opp_pos)
        opp_to_target = dist2(opp_pos, (tx, ty))
        # Bias: smaller is better; add small deterministic term to break ties.
        score = cur - 0.15 * opp + 0.05 * opp_to_target + 1e-6 * (nx * 9 + ny)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]
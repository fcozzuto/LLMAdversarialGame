def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Deterministic move preference order: stay, then closer diagonals/axes to target.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Pick a target we can reach relatively sooner than opponent.
        best = None
        for tx, ty in resources:
            sd = man((sx, sy), (tx, ty))
            od = man((ox, oy), (tx, ty))
            # Reward being closer; also add small bias toward slightly nearer absolute targets.
            score = (od - sd) * 2.5 - sd * 0.15 - tx * 0.001 - ty * 0.001
            if best is None or score > best[0] or (score == best[0] and (tx, ty) < best[1]):
                best = (score, (tx, ty))
        tx, ty = best[1]
    else:
        tx, ty = w // 2, h // 2

    # Choose next step that most reduces distance to target; penalize moves allowing opponent to get closer.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd_next = man((nx, ny), (tx, ty))
        od = man((ox, oy), (tx, ty))
        # Opponent-availability penalty: discourage moving to squares that keep us farther than opponent.
        rel_pen = (sd_next - od)
        val = -sd_next - rel_pen * 0.35
        # Small deterministic tie-break: prefer actions with smaller change first in deltas order already.
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move
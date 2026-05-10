def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or (self_role == "evader")
    # Default to pursuer unless clearly evader
    if "pursuer" in self_role or self_role == "pursuer":
        is_evader = False
    if "evader" not in self_role and "pursuer" not in self_role:
        is_evader = False

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def block_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        pen = 0
        for (bx, by) in obstacles:
            md = abs(x - bx) + abs(y - by)
            if md == 0:
                return 10**9
            if md == 1:
                pen += 6
            elif md == 2:
                pen += 2
        return pen

    best = None
    best_score = None
    tie = 0
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        p = block_pen(nx, ny)
        if p >= 10**8:
            continue
        d = dist(nx, ny, ox, oy)

        # Heuristic: stay out of opponent's direct approach for evader; close distance for pursuer.
        # Interception bias for pursuer: prefer moves that reduce the max coordinate gap.
        coord_gap = max(abs(ox - nx), abs(oy - ny))
        approach_dir = (0 if ox == nx else (1 if ox > nx else -1), 0 if oy == ny else (1 if oy > ny else -1))
        dot = (dx * approach_dir[0] + dy * approach_dir[1])  # in [-2,2]
        center_bias = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) * 1e-3

        if is_evader:
            score = d * 2.0 + coord_gap * 0.4 + dot * 0.3 + center_bias - p * 3.0
        else:
            score = -d * 2.0 - coord_gap * 0.6 + dot * 0.2 + center_bias - p * 3.0

        # Deterministic tie-breaker: prefer moves in a fixed order (deltas order), then lower tie counter.
        if best_score is None or score > best_score + 1e-9:
            best_score = score
            best = (dx, dy)
            tie = 0
        elif abs(score - best_score) <= 1e-9 and tie == 0:
            best = (dx, dy)
            tie = 1

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
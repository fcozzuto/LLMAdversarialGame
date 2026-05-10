def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role_self = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role_self) or ("hunter" in role_self) or ("chaser" in role_self)
    # If role naming is ambiguous, infer from capture direction: pursuer is usually closer to getting capture points
    if not pursuer and "evader" in role_self:
        pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def obst_adj(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    cnt += 1
        return cnt

    # Heuristic target:
    # pursuer: aim to reduce distance; prefer moves that also align with the opponent
    # evader: aim to increase distance; prefer moves that move away and reduce adjacency to obstacles
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist2(nx, ny, ox, oy)
        # alignment: compare direction components to opponent relative position
        rx, ry = ox - nx, oy - ny
        step_align = (1 if rx > 0 else -1 if rx < 0 else 0, 1 if ry > 0 else -1 if ry < 0 else 0)
        # If aligned, dist reduction is likely
        align_bias = (step_align[0] == (1 if dx > 0 else -1 if dx < 0 else 0)) + (step_align[1] == (1 if dy > 0 else -1 if dy < 0 else 0))
        oa = obst_adj(nx, ny)
        if pursuer:
            score = (-d) + 0.7 * align_bias - 0.15 * oa
        else:
            score = d + 0.35 * align_bias - 0.25 * oa
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        # All moves blocked: deterministic stay
        return [0, 0]
    return [int(best[0]), int(best[1])]
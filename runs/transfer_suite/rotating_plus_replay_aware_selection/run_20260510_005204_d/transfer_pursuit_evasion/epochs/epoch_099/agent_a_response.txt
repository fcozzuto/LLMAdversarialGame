def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    env = str(observation.get("environment_name", "")).lower()
    is_evader = any(k in role for k in ["evader", "runner", "evade", "escape"]) or any(
        k in env for k in ["evader", "runner", "evade", "escape"]
    )

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Evader: maximize distance from pursuer; also prefer getting to a corner farthest from pursuer.
    # Pursuer: minimize distance to evader; also prefer cornering by targeting the evader-farthest corner.
    if is_evader:
        target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            d_foe = dist2(nx, ny, ox, oy)
            d_corner = dist2(nx, ny, target_corner[0], target_corner[1])
            score = (d_foe, -d_corner)  # lexicographic via tuple compare
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        if best is not None:
            return [best[0], best[1]]
        return [0, 0]
    else:
        target_corner = max(corners, key=lambda c: dist2(c[0], c[1], sx, sy))  # fallback: far from self
        target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))  # evader farthest corner
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            d_to_evader = dist2(nx, ny, ox, oy)
            d_to_corner = dist2(nx, ny, target_corner[0], target_corner[1])
            # Primary: get close to evader. Secondary: align toward corner.
            score = (-d_to_evader, -d_to_corner)
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        if best is not None:
            return [best[0], best[1]]
        return [0, 0]
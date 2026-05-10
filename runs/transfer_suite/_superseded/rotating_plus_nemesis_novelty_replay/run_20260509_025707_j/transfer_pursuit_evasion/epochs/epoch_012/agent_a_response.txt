def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position")
    op = observation.get("opponent_position")
    if not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = (role == "evader")

    nearest_corner_to_opp = min(corners, key=lambda c: man(ox, oy, c[0], c[1]))
    farthest_corner_from_opp = max(corners, key=lambda c: man(ox, oy, c[0], c[1]))
    target = farthest_corner_from_opp if is_evader else nearest_corner_to_opp

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dx, best_dy = 0, 0
    if is_evader:
        best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_opp = man(nx, ny, ox, oy)
            d_tar = man(nx, ny, target[0], target[1])
            val = 3.0 * d_opp + 0.6 * d_tar
            # Wall runner bias: keep moving roughly away from opponent along the largest component
            awayx = 0 if ox == nx else (1 if ox < nx else -1)
            awayy = 0 if oy == ny else (1 if oy < ny else -1)
            val += 0.4 * (dx * awayx + dy * awayy)
            if val > best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
                best_val = val
                best_dx, best_dy = dx, dy
    else:
        best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_opp = man(nx, ny, ox, oy)
            d_tar = man(nx, ny, target[0], target[1])
            # Pursuer bias: minimize distance to opponent, and also align to cut off via corner target
            val = -2.8 * d_opp - 0.8 * d_tar
            # If multiple moves tie, prefer moving closer along each axis (more direct)
            val += 0.15 * (abs(ox - sx) + abs(oy - sy) - (abs(ox - nx) + abs(oy - ny)))
            if val > best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
                best_val = val
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]
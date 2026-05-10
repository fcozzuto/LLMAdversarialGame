def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = any(k in role for k in ["evader", "runner", "evade", "escape"])
    env = str(observation.get("environment_name", "")).lower()
    if any(k in env for k in ["evader", "runner", "evade", "escape"]):
        is_evader = True

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def clamp_move(x, y):
        if inb(x, y) and (x, y) not in blocked:
            return True
        return False

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Evader target: corner that is farthest from pursuer (opponent).
    # Pursuer target: the pursuer "line" toward the evader's farthest corner to corner them.
    if is_evader:
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        aimx, aimy = tx, ty
    else:
        # Estimate evader's likely retreat corner by farthest from us.
        ex, ey = max(corners, key=lambda c: dist2(c[0], c[1], sx, sy))
        aimx, aimy = ex, ey

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not clamp_move(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        # Chebyshev-like progress via signed deltas to the aim point.
        cur_to_aim = (sx - aimx) * (sx - aimx) + (sy - aimy) * (sy - aimy)
        nxt_to_aim = (nx - aimx) * (nx - aimx) + (ny - aimy) * (ny - aimy)

        # Small deterministic tie-breaker preferring not to stay still unless necessary.
        moved = 0 if (dx == 0 and dy == 0) else 1

        if is_evader:
            # Maximize survival: increase distance from opponent; also keep moving away from aim corner of pursuer estimate.
            score = d_opp + 0.3 * (cur_to_aim - nxt_to_aim) + 0.05 * moved
        else:
            # Capture strategy: reduce distance to opponent primarily; also reduce distance to estimated retreat corner.
            score = -d_opp + 0.15 * (cur_to_aim - nxt_to_aim) + 0.05 * moved

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best
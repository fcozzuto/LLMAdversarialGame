def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best = None
    best_dxdy = [0, 0]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-breaking: iterate fixed move order; keep first max/min.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # Small corner pressure to reduce escape routes (pursuer) / improve hiding (evader)
        corner_dist = min(cheb(nx, ny, cx, cy) for cx, cy in corners)
        d_to_opp_corners = min(cheb(cx, cy, ox, oy) for cx, cy in corners)
        # Heuristic:
        # pursuer: minimize d, and prefer being closer to corners that are closer to opponent
        # evader: maximize d, and prefer being in corners that are farther from opponent
        val = (-d) + (0.05 * (corner_dist if is_evader else -corner_dist)) + (0.02 * (d_to_opp_corners if not is_evader else -d_to_opp_corners))
        if best is None:
            best = val
            best_dxdy = [dx, dy]
        else:
            if is_evader:
                if val > best:
                    best = val
                    best_dxdy = [dx, dy]
            else:
                if val > best:
                    best = val
                    best_dxdy = [dx, dy]

    # If all moves invalid (should be rare), stay.
    return best_dxdy
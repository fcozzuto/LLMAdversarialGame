def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax - bx), abs(ay - by))
    def valid(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obs and (nx, ny) != (ox, oy)
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    my = (sx, sy); opp = (ox, oy)
    # Prefer resources where we can arrive earlier than opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        me_pos = (nx, ny)
        # Base pressure: get away from opponent if it threatens.
        opp_now = dist(my, opp)
        opp_next = dist(me_pos, opp)
        score = 0.0
        if opp_next <= 1:
            score += 6.0  # avoid getting too close
        score += (opp_next - opp_now) * 0.5  # slight tendency to increase distance
        if res:
            # Composite over resources: smaller is better
            best_r = None
            for rx, ry in res:
                r = (rx, ry)
                d_me = dist(me_pos, r)
                d_opp = dist(opp, r)
                # Want: small d_me, large (d_opp - d_me)
                # Also slight preference for closer resources generally.
                pr = (d_me * 1.2) + max(0, d_me - d_opp) * 2.0 - max(0, d_opp - d_me) * 0.8
                if best_r is None or pr < best_r:
                    best_r = pr
            score += best_r
        else:
            score += dist(me_pos, (0, 0)) * 0.1  # fallback: drift toward corner
        # Tie-break deterministically: lexicographic by dx,dy order in moves
        if best_score is None or score < best_score - 1e-9:
            best_score = score
            best_move = (dx, dy)
        elif abs(score - best_score) <= 1e-9:
            if (dx, dy) < best_move:
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]
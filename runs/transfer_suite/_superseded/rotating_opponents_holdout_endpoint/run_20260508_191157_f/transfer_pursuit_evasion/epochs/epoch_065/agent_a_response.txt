def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = (observation.get("self_role") or "pursuer").lower()
    pursuer = (role == "pursuer")

    cands = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def best_corner(target_toward_opponent):
        # target_toward_opponent True: choose corner closest to opponent; else farthest
        if target_toward_opponent:
            return min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        return max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    corner = best_corner(pursuer)
    best_move = (0, 0)
    best_score = None

    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d_op = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, corner[0], corner[1])

        # Prefer blocking corner approach when pursuer, and escape toward far corner when evader.
        if pursuer:
            # minimize distance to opponent; break ties by moving toward the chosen corner
            score = (d_op, d_corner)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # maximize distance from opponent; break ties by moving away from corner
            score = (-d_op, -d_corner)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
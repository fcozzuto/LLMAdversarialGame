def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((a, b) for a, b in observation["obstacles"])
    resources = observation["resources"]

    def inb(px, py):
        return 0 <= px < w and 0 <= py < h

    def cheb(px, py, qx, qy):
        dx = px - qx
        if dx < 0:
            dx = -dx
        dy = py - qy
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_delta = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if nx == ox and ny == oy:
            continue

        if not resources:
            d_opp = cheb(nx, ny, ox, oy)
            score = (-d_opp, 0)
        else:
            best_res = None
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                adv = d_self - d_opp  # negative is good
                key = (adv, d_self, d_opp)
                if best_res is None or key < best_res:
                    best_res = key
            adv, d_self, d_opp = best_res
            # Prefer capturing sooner (small d_self), also prefer outpacing opponent (small adv)
            score = (adv, d_self, -d_opp, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]
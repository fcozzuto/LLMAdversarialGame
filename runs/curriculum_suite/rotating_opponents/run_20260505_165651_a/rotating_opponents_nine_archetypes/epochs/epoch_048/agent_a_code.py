def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    opp_d0 = king_dist(sx, sy, ox, oy)

    center_x = (w - 1) // 2
    center_y = (h - 1) // 2

    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if resources:
            val = 0.0
            for rx, ry in resources:
                our_d = king_dist(nx, ny, rx, ry)
                opp_d = king_dist(ox, oy, rx, ry)

                # Strong preference for resources we can reach sooner than opponent.
                # If we can beat them, add a large value scaled by how quickly.
                if our_d < opp_d:
                    beat = (opp_d - our_d)
                    val += 50.0 * beat / (1.0 + our_d)
                else:
                    # If we can't beat them, still partially value shrinking their lead.
                    val += 8.0 * (opp_d - our_d) / (1.0 + our_d)

                # Avoid moving into a state where opponent's distance to many resources drops.
                # (Heuristic anti-sweep: reduce cases where we "open" targets for them.)
                if our_d <= 2:
                    val += 1.5 / (1.0 + our_d)

            # Mild tie-break: keep some pressure near opponent without enabling immediate contest collapse.
            val += 0.5 * (opp_d0 - king_dist(nx, ny, ox, oy))
            # Mild tie-break: centralize if values are close.
            val += -0.01 * (abs(nx - center_x) + abs(ny - center_y))
        else:
            # No visible resources: drift to center.
            val = -abs(nx - center_x) - abs(ny - center_y)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def kingd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    scored = []
    opp_now = kingd(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            best = -1e9
            for rx, ry in resources:
                ds = kingd(nx, ny, rx, ry)
                do = kingd(ox, oy, rx, ry)

                # Primary: how much we out-race opponent to this resource.
                # Negative of (our dist - opp dist) => larger is better.
                race = (do - ds)

                # Secondary: prefer closer overall to reduce opponent "sniping" window.
                closeness = -0.15 * ds

                # Tertiary: add slight bias away from giving opponent immediate advantage.
                # If opponent is much closer, don't go there unless we're also very close.
                risk = -0.25 * max(0, ds - do)

                v = race + closeness + risk
                if v > best:
                    best = v

            # Add a small term to keep pressure on the opponent position.
            # (Ensures meaningful change when race ties.)
            v = best + 0.02 * (kingd(ox, oy, nx, ny) - opp_now)
        else:
            # No resources observed: drift toward center while avoiding obstacles.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            v = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        scored.append((v, dx, dy))

    if not scored:
        return [0, 0]
    scored.sort(key=lambda t: (t[0], -abs(t[1]) - abs(t[2]), t[1], t[2]))
    return [scored[-1][1], scored[-1][2]]
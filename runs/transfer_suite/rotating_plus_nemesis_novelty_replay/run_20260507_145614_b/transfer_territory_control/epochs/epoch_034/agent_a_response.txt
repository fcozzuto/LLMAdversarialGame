def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p[:2]) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p[:2]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    my_terr = set(tuple(p[:2]) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set(tuple(p[:2]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_list = list(opp_terr)
    un_list = list(unclaimed)
    has_opp = len(opp_list) > 0
    has_un = len(un_list) > 0

    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Base value: claim/flip incentives
        val = 0.0
        if (nx, ny) in my_terr:
            val += 0.6
        if (nx, ny) in unclaimed:
            val += 2.0
        if (nx, ny) in opp_terr:
            val += 8.0  # flipping on entry

        # Strategic pressure: control unclaimed while staying away from opponent bulk unless flipping
        if has_un:
            d_un = min(man(nx, ny, ux, uy) for ux, uy in un_list)
            val += 1.4 / (1 + d_un)
        if has_opp:
            d_opp = min(man(nx, ny, px, py) for px, py in opp_list)
            val += 0.9 * (d_opp / 8.0)  # prefer distance from opponent edge-claiming

            # Penalize being adjacent to opponent territory (likely to be flipped/contested next)
            adj_opp = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in opp_terr:
                        adj_opp += 1
            val -= 0.35 * adj_opp

        # Mild tie-break toward advancing away from our starting corner? Use opponent position to bias lanes
        # (deterministic and cheap)
        lane = man(nx, ny, ox, oy) - man(sx, sy, ox, oy)
        val += 0.25 * lane

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]